# Response structure for the fetch call
httpResponse = {
    "status": 200,
    "message": "Success",
    "description": "",
    "data": {
        "playlist_id": "",
        "num_videos": "",
        "total_runtime": "",
        "avg_runtime": "",
        "metadata": {
            "version": "v1",
            "offered_by": "Enrich Platforms",
            "additional_info": "",
        }
    }
}


# To parse the datetime object into readable time
def parse(runtime):
    ts, td = runtime.seconds, runtime.days
    th, tr = divmod(ts, 3600)
    tm, ts = divmod(tr, 60)
    ds = ''
    if td:
        ds += ' {} day{},'.format(td, 's' if td != 1 else '')
    if th:
        ds += ' {} hour{},'.format(th, 's' if th != 1 else '')
    if tm:
        ds += ' {} minute{},'.format(tm, 's' if tm != 1 else '')
    if ts:
        ds += ' {} second{}'.format(ts, 's' if ts != 1 else '')
    if ds == '':
        ds = '0 seconds'
    return ds.strip().strip(',')
