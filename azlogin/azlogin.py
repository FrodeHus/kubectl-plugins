#!/usr/bin/env python3
import adal
import sys
import json
import pathlib
import subprocess
from os import getenv

CACHEFILE = ".tokencache"

class TokenHelper(object):

    def __init__(self, client_id, app_id, authority):
        self._app_id = app_id
        self._client_id = client_id

        self._cache = self._load_cache()
        self._context = adal.AuthenticationContext(authority, cache=self._cache, api_version=None)

    def _load_cache(self):
        cache = adal.TokenCache()
        file = pathlib.Path(CACHEFILE)
        if not file.is_file():
            return cache
        with file.open() as data:
            cache.deserialize(data.read())
        return cache

    def _save_cache(self):
        if not self._cache:
            return

        cached = self._cache.serialize()
        with open(CACHEFILE, "w") as out:
            out.write(cached)

    def get_token(self, user):
        token = None
        if user:
            print("Requesting token for {} using cache...".format(user))
            token = self._context.acquire_token(self._app_id, user, self._client_id)
            if token is None:
                print("User not found or token expired...")
                token = self.get_token_using_device_code()
        else:
            token = self.get_token_using_device_code()
        self._save_cache()
        return token

    def get_token_using_device_code(self):
        code = self._context.acquire_user_code(self._app_id, self._client_id)
        print(code['message'])
        token = self._context.acquire_token_with_device_code(self._app_id, code, self._client_id)
        return token

def main():
    tenantId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_TENANT")
    appId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_APPID")
    clientId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_CLIENTID")
    user = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_USER", None)

    helper = TokenHelper(clientId, appId, "https://login.microsoftonline.com/" + tenantId)
    token = helper.get_token(user)
    if token is None:
        print("Failed to retrieve token")
        sys.exit(1)

    accessToken = token["accessToken"]
    userId = token["userId"]
    subprocess.call(["kubectl", "config", "set-credentials", userId, "--token", accessToken])

if __name__ == "__main__":
    main()
