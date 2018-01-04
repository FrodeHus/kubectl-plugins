#!/usr/bin/env python3
import adal
import sys
import json
import pathlib
import subprocess
from os import getenv

class TokenHelper(object):
    def __init__(self, client_id, app_id, authority):
        self._app_id = app_id
        self._client_id = client_id
        adal.oauth2_client.TOKEN_RESPONSE_MAP = {'resource': 'resource', 'access_token': 'accessToken', 'error_description': 'errorDescription', 'error': 'error', 'expires_in': 'expiresIn', 'expires_on': 'expiresOn', 'token_type': 'tokenType', 'created_on': 'createdOn', 'refresh_token': 'refreshToken', 'id_token': 'idToken'}

        self._cache = self._load_cache()
        self._context = adal.AuthenticationContext(authority, cache=self._cache, api_version=None)

    def _load_cache(self):
        cache = adal.TokenCache()
        file = pathlib.Path(".tokencache")
        if not file.is_file():
            return cache
        data = file.read_text()
        cache.deserialize(data)
        return cache

    def get_token_using_device_code(self):
        code = self._context.acquire_user_code(self._app_id, "28700222-ef32-4a52-a003-5e0ddc134b26")
        print(code['message'])
        token = self._context.acquire_token_with_device_code(self._app_id, code, self._client_id)
        return token

def main():
    user = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_USER")
    tenantId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_TENANT")
    appId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_APPID")
    clientId = getenv("KUBECTL_PLUGINS_LOCAL_FLAG_CLIENTID")

    helper = TokenHelper(clientId, appId, "https://login.microsoftonline.com/" + tenantId)
    token = helper.get_token_using_device_code()
    idToken = token["idToken"]
    subprocess.run(["kubectl", "config", "set-credentials", user, "--token", idToken])

if __name__ == "__main__":
    main()
