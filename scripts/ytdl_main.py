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




def main():
    """ main function """
    print("YOUTUBE-DL BASED DOWNLOADER")
    print("by: github.com/kithstack1")
    query = input("Enter the url or search term: ")
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
    if download_best == 'y':
       download_best = True
    else:
        download_best = False
    if not download_best:
        available_formats = results[choice-1]['formats']
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
    else:
        format_code = 22 if media_type == 'video' else 140
        extention = 'mp4' if media_type == 'video' else 'mp3'
        quality = 'best'
    # store options in a dictionary
    ydl_opts = {"format": str(format_code), "outtmpl": f"{output_dir}/{result['title']}.{extention}", "quiet": True, "quality": quality,"extention": extention}
    # download video or audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([results[choice-1]['webpage_url']])
    print("Download complete")



if __name__ == "__main__":
    main()
