import aiohttp
import asyncio
import time

start_time = time.time()


async def get_pokemon(session,url):
    async with session.get(url) as resp:
        pokemon = await resp.json()
        return pokemon["name"]


async def main():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=64,verify_ssl=False)) as session:

            tasks = []
            for i in range(1,200):
                pok_url = f"https://pokeapi.co/api/v2/pokemon/{i}"
                tasks.append(asyncio.ensure_future(get_pokemon(session,pok_url)))

            original_pokemon = await asyncio.gather(*tasks)
            for pok in original_pokemon:
                print(pok)

asyncio.run(main())
print(f"--{(time.time()-start_time)}--")