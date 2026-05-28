const ASSETS = new Set(["install.sh", "version.json", "hplan-package.tar.gz"]);
const R2_PREFIX = "hplan";

export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return text("Method not allowed", 405);
    }

    const url = new URL(request.url);
    const route = parseRoute(url);

    if (!route) {
      return text("Not found", 404);
    }

    if (route.asset === "health") {
      return json({ ok: true, service: "hplan-installer" });
    }

    const auth = authorize(request, url, env, route.token);
    if (!auth.ok) {
      return text(auth.message, auth.status);
    }

    const asset = await loadAsset(request, url, env, route);
    if (!asset) {
      return text(`Missing hplan asset: ${route.asset}`, 404);
    }

    const headers = baseHeaders(route.asset, asset.headers);
    if (route.asset === "install.sh") {
      const script = await asset.response.text();
      const rendered = script.replaceAll(
        "https://habix.ai/hplan",
        route.baseUrl
      );
      return new Response(request.method === "HEAD" ? null : rendered, {
        headers,
      });
    }

    return new Response(request.method === "HEAD" ? null : asset.response.body, {
      headers,
    });
  },
};

async function loadAsset(request, url, env, route) {
  if (env.ASSETS) {
    const assetUrl = new URL(url);
    assetUrl.pathname = `/${R2_PREFIX}/${route.asset}`;
    assetUrl.search = "";
    const response = await env.ASSETS.fetch(
      new Request(assetUrl.toString(), request)
    );
    if (response.ok) {
      return { response, headers: response.headers };
    }
  }

  if (env.HPLAN_R2) {
    const key = `${R2_PREFIX}/${route.asset}`;
    const object = await env.HPLAN_R2.get(key);
    if (object) {
      return {
        response: new Response(object.body),
        headers: object.httpMetadata || new Headers(),
      };
    }
  }

  return null;
}

function parseRoute(url) {
  const parts = url.pathname.split("/").filter(Boolean);
  if (parts[0] !== "hplan") {
    return null;
  }

  if (parts.length === 1) {
    return {
      asset: "install.sh",
      token: null,
      baseUrl: `${url.origin}/hplan`,
    };
  }

  if (parts[1] === "health") {
    return {
      asset: "health",
      token: null,
      baseUrl: `${url.origin}/hplan`,
    };
  }

  if (ASSETS.has(parts[1])) {
    return {
      asset: parts[1],
      token: null,
      baseUrl: `${url.origin}/hplan`,
    };
  }

  const token = parts[1];
  const asset = parts[2] || "install.sh";
  if (!ASSETS.has(asset)) {
    return null;
  }

  return {
    asset,
    token,
    baseUrl: `${url.origin}/hplan/${token}`,
  };
}

function authorize(request, url, env, routeToken) {
  const expected = env.HPLAN_ACCESS_TOKEN || "";
  if (!expected) {
    return { ok: true };
  }

  const provided =
    routeToken ||
    url.searchParams.get("t") ||
    request.headers.get("x-hplan-token") ||
    "";

  if (provided === expected) {
    return { ok: true };
  }

  return {
    ok: false,
    status: 403,
    message: "Invalid or missing hplan access token",
  };
}

function baseHeaders(asset, sourceHeaders = new Headers()) {
  const contentType = {
    "install.sh": "text/x-shellscript; charset=utf-8",
    "version.json": "application/json; charset=utf-8",
    "hplan-package.tar.gz": "application/gzip",
  }[asset] || sourceHeaders.get("content-type") || "application/octet-stream";

  const cacheControl =
    asset === "hplan-package.tar.gz"
      ? "private, max-age=300"
      : "no-store";

  return {
    "content-type": contentType,
    "cache-control": cacheControl,
    "x-content-type-options": "nosniff",
  };
}

function text(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}
