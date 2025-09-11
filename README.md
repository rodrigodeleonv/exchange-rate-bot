# exchange-rate-bot

## References

- [Nexa Banco](https://www.nexabanco.com/)


## aiohttp

[aiohttp client quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)

Note
Don’t create a session per request. Most likely you need a session per application which performs all requests together.

More complex cases may require a session per site, e.g. one for Github and other one for Facebook APIs. Anyway making a session for every request is a very bad idea.

A session contains a connection pool inside. Connection reusage and keep-alive (both are on by default) may speed up total performance.

