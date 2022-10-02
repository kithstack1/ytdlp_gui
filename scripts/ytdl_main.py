""" 
entry script for youtube-dl based downloader
features:
    - download from youtube
    - download from soundcloud
    - download from bandcamp
    - download from vimeo
    - download from archive.org
    - download from mixcloud
    - download from spotify
      and many more
cli script aimed at ease of use
"""
import yt_dlp
import os 
import tabulate
import re


def clean_up(query):
    """ clean up query """
    illegal_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "=", "+", "[", "]", "{", "}", ";", ":", "'", '"', ",", "<", ">", ".", "?", "/", "\\", "|"]
    for char in illegal_chars:
        query = query.replace(char, "")
    return query

def extract_info(query: str,num_results: int) -> list:
    """ extract info from query
    params:
      query (str): query to search for
      num_results (int): number of results to return
    """

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        results = ydl.extract_info(f"ytsearch{num_results}:{query}", download=False)['entries']
    return results


def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }




def is_supported(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return (True, e.IE_NAME)
    return False, None




def main():
    """ main function """
    print("YOUTUBE-DL BASED DOWNLOADER")
    print("by: github.com/kithstack1")
    # print in a table format the first 10 extractors available in yt-dlp
    print('extractors available include but not limited to: ')
    extractors = yt_dlp.list_extractors()
    extractor_names = [extractor.IE_NAME for extractor in extractors][:10]
    headers = ['index', 'extractor']
    table = [[index, extractor] for index, extractor in enumerate(extractor_names)]
    print(tabulate.tabulate(table, headers=headers, tablefmt='grid'))
    query = input("Enter the url or search term: ")
    # query might be a url or a search term so pass it to is_supported to check
    supported, extractor = is_supported(query)
    # if the url is supported and it aint from youtube, then just download it with yt_dlp
    if supported and extractor != 'Youtube':
        print(f'Detected url from {extractor.upper()}')
        print('[+] downloading...')
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.download([query])
            return 
    query = clean_up(query)
    print('query: ' + query)
    print('Do you want the first result?')
    first_result = input('y/n: ')
    if first_result == 'y':
        first_result = True
    else:
        first_result = False
    num = int(input("Enter the number of results to search: ")) if not first_result else 1  # noqa: E501

    # search for query using yt-dlp and return all results
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        if first_result:
            results = extract_info(query, 1)
            while not results:
                print('No results found. Try again.')
                query = input("Enter the url or search term: ")
                query = clean_up(query)
                print('query: ' + query)
                results = extract_info(query, 1)
        else:
            results = extract_info(query, num)
            while not results:
                print("No results found, try again with a different query")
                query = input("Enter the url or search term: ")
                query = clean_up(query)
                print('query: ' + query)
                num = int(input("Enter the number of results to search: "))
                results = extract_info(query, num)
    for i, result in enumerate(results):
        print(f"{i+1}: {result['title']}")
    if len(results) == 1:
        choice = 1
    else:
        choice = int(input("Enter the number of the result you want to download: "))
   
    media_type = input("Enter the media type (audio/video): ")
    output_dir = input("Enter the output directory: ")

    # get additional options
    download_best = input("Download best quality? (y/n): ")
    write_subs = input("Write subtitles? (y/n): ")
    write_subs = True if write_subs == 'y' else False 
    if download_best == 'y':
       download_best = True
    else:
        download_best = False
    available_formats = results[choice-1]['formats']
    format_codes = [format['format_id'] for format in available_formats]
    if not download_best:
        headers = 'Index Format Extension Resolution note'.split(' ')
        table = []
        for i, format in enumerate(available_formats):
            row = [f"{i+1}",format['format_id'],format['ext'],format['resolution'],format['format_note']]
            table.append(row)
        print(tabulate.tabulate(table, headers, tablefmt="grid"))
        format_choice = int(input("Enter the number of the format you want to download: "))
        format_code  = available_formats[format_choice-1]['format_id']
        extention = available_formats[format_choice-1]['ext']
        quality = available_formats[format_choice-1]['format_note']
        ydl_opts = {"format": str(format_code), "outtmpl": f"{output_dir}/{result['title']}.{extention}", "quiet": True, "quality": quality,"extention": extention, "writeautomaticsub": write_subs}
    else:
        ydl_opts = {'format': format_selector, "outtmpl": f"{output_dir}/{result['title']}.%(ext)s", "quiet": True, "writeautomaticsub": write_subs}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([results[choice-1]['webpage_url']])
    print("Download complete")



if __name__ == "__main__":
    main()
