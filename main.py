import os
import time

from KalturaClient import *
from KalturaClient.Plugins.Core import *

def K_connect():
    config = KalturaConfiguration(4530233)
    config.serviceUrl = "https://www.kaltura.com/"
    client = KalturaClient(config)

    secret = "fe3397b78566adecf8de92e4ae747d3d"
    user_id = "joshcaton@live.com"
    k_type = KalturaSessionType.ADMIN
    partner_id = "4530233"
    expiry = 86400
    privileges = ""

    ks = client.session.start(secret, user_id, k_type, partner_id, expiry, privileges)
    client.setKs(ks)

    print("KalturaClient connection started")

    return client

def uploadVideoFiles(client, file_list):

    resume = False
    final_chunk = True
    resume_at = -1
    name_list = [s.replace('.mp4', '') for s in file_list]
    desc_list = ['A sample video file of ' + s + ' from Wikimedia Commons' for s in name_list]
    ent_ids = {}

    for i in range(len(file_list)):
        print('Uploading ' + str(file_list[i]))

        #get new upload token
        upload_token = KalturaUploadToken()
        token = client.uploadToken.add(upload_token)

        #upload video file
        upload_token_id = token.id
        file_data =  open('C:/video/' + file_list[i], 'rb')
        upload_response = client.uploadToken.upload(upload_token_id, file_data, resume, final_chunk, resume_at)

        #upload metadata
        entry = KalturaMediaEntry()
        entry.mediaType = KalturaMediaType.VIDEO
        entry.name = name_list[i]
        entry.description = desc_list[i]
        mediaAdd_response = client.media.add(entry)

        #capture entry id
        ent_ids[i] = (mediaAdd_response.id)

        #associate metadata with uploaded video
        resource = KalturaUploadedFileTokenResource()
        resource.token = upload_token_id
        result = client.media.addContent(mediaAdd_response.id, resource)
    else:
        return ent_ids

def createCategories(client):
    cat_ids = []
    category1 = KalturaCategory()
    category1.name = "First Category"
    resp_category_1 = client.category.add(category1)
    cat_ids.append(resp_category_1.id)

    category2 = KalturaCategory()
    category2.name = "Second Category"
    resp_category_2 = client.category.add(category2)
    cat_ids.append(resp_category_2.id)

    return cat_ids

def associateCategories(client, cat_ids, ent_ids):
    current_entry_index = 0
    for x in range(len(cat_ids)):
        for i in range(5):
            print('Adding vid_id ' + str(ent_ids[current_entry_index]) + ' to category ' + str(cat_ids[x]))
            category_entry = KalturaCategoryEntry()
            category_entry.categoryId = cat_ids[x]
            category_entry.entryId = ent_ids[current_entry_index]
            result = client.categoryEntry.add(category_entry)
            current_entry_index += 1

def main():
    #start execution timer
    start_time = time.time()

    #prepare file array
    fl = os.listdir('C:/video')

    #establish connection
    c = K_connect()

    e_ids = uploadVideoFiles(c, fl)
    c_ids = createCategories(c)
    associateCategories(c, c_ids, e_ids)

    #cleanup session
    c.session.end()

    #output total time
    print("--- Finished --- %s was total run time ---" % (time.time() - start_time))

main()
