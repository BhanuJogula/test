from genericpath import exists
from fastapi import APIRouter, Request, HTTPException
import app.clients.bifrost.user as bifrost
import app.database.database as db

router = APIRouter()

@router.get("/v1/thumbnail/hello")
async def get_thumbnail_sso(request: Request):
    return {
        "str" : "Welcome to FASTAPPI" }

@router.post("/v1/thumbnail/generate-screenshot")
async def post_thumbnail_generate_screenshot(request: Request):
    thumbnail_client = await bifrost.Thumbnail.from_http(http_request=request)
    req_args = await thumbnail_client.args()
    result = await submit_bifrost_request(thumbnail_client, req_args['site_url'])
    return result

async def submit_bifrost_request(thumbnail_client, site_url, force_override=False):
    
    result = await thumbnail_client.call("thumbnail",
                                       args={"url":site_url, "force_override":force_override})
    return result


@router.get("/v1/thumbnail/get-screenshot")
async def get_thumbnail_get_screenshot(request: Request):
    thumbnail_client = await bifrost.Thumbnail.from_http(http_request=request)
    req_args = await thumbnail_client.args()
    force_override = "false"
    if req_args['force_override']:
        force_override = req_args['force_override']

    rec_exists = 1
    if req_args['site_url']:
        site_url = req_args['site_url']

        if (not site_url.startswith('http')):
            raise HTTPException(404, "Invalid Site URL")

        if (site_url.endswith('/')):
            site_url = site_url.rstrip(site_url[-1])
        
        if force_override != "true":
            try:
                sql_stmt = "select thumbnail_location from SITE_THUMBNAIL_INFO where site_url = %s and last_modified_date > (NOW() - INTERVAL 24 HOUR)"
                values = (site_url,) 
                result = db.fetch_data(sql_stmt, values)
                return {
                    "thumbnail_loc": result[-1][-1],
                    "msg" : "Thumbnail already exists"
                }
            except:
                rec_exists = 0

        if rec_exists == 0 or force_override == "true":
            result = await submit_bifrost_request(thumbnail_client, req_args['site_url'], force_override)
            return {
                "thumbnail_loc": '',
                "msg" : result 
            }
  
@router.post("/v1/thumbnail/update-screenshot")
async def post_thumbnail_update_screenshot(request: Request):
    thumbnail_client = await bifrost.Thumbnail.from_http(http_request=request)

    req_args = await thumbnail_client.args()
    if len(req_args['successful']) > 0 and req_args['successful'][0]['url']:
         try:
            site_url = req_args['successful'][0]['websiteUrl']
            if (site_url.endswith('/')):
                site_url = site_url.rstrip(site_url[-1])
            if (site_url.startswith('http')):
                sql_stmt = "select count(1) from SITE_THUMBNAIL_INFO where site_url = %s"
                values = (site_url,) 
                info_exits = db.data_exits(sql_stmt, values)
                if info_exits == 0:
                    sql_stmt = "INSERT INTO SITE_THUMBNAIL_INFO (thumbnail_id, site_url, thumbnail_location, last_modified_date) VALUES (NULL, %s, %s, NOW())"
                    values= (site_url, req_args['successful'][0]['url'])
                else:
                    sql_stmt = "update SITE_THUMBNAIL_INFO set thumbnail_location = %s, last_modified_date = NOW() where site_url = %s"
                    values= (req_args['successful'][0]['url'], site_url)
                
                db.insert_update_data(sql_stmt, values)
            else:
               raise HTTPException(404, "Invalid Site URL")
         except:
            raise
 
    return {
        "msg" : "Updated the screenshot information" }