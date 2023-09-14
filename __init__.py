import logging

from aiohttp import web
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError

from .group_data import get_group_data

logger = logging.getLogger('luoxu_plugins.analytics')


class GroupAnalyticsHandler:
    def __init__(self, client):
        self.client = client

    async def get(self, request: web.Request):
        if cid_str := request.match_info.get('cid'):
            try:
                uid = int(cid_str)
                await self.client.get_entity(uid)
            except (ValueError, ChannelPrivateError):
                raise web.HTTPForbidden(headers={
                    'Cache-Control': 'public, max-age=86400',
                })
            return web.json_response(await get_group_data(uid, self.client))
        else:
            raise web.HTTPNotFound


async def register(indexer, client: TelegramClient):
    port: int = int(indexer.config['plugin_analytics']['port'])

    handler = GroupAnalyticsHandler(client)

    app = web.Application()
    app.router.add_get('/api/group_analytics', handler.get)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        '127.0.0.1', port,
    )
    await site.start()
