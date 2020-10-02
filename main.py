from yandex_music.client import Client, Track
import os
import yandex_music
from pprint import pprint
import json
from collections import OrderedDict


class Ya_Client:
    def __init__(self, token):
        self.client = Client.from_token(token)
        self.liked_tracks_dict = OrderedDict()
        self.liked_tracks_list = list()
        self.tracks = self.client.users_likes_tracks()
        self.load_liked_tracks_json()
        self.settings_dict = {}

    def load_liked_tracks_json(self):
        try:
            with open('tracks.json', 'r') as fp:
                self.liked_tracks_dict = json.load(
                    fp, object_pairs_hook=OrderedDict)
        except FileNotFoundError:
            self.update_liked_tracks()

    def download_liked_tracks(self, dir_name=None):
        tracks = self.client.users_likes_tracks()
        print("\n\n")
        print(dir_name)
        i = 0

        if dir_name is not None:
            os.mkdir(f"./{dir_name}")
            os.chdir(f"./{dir_name}")
        num_of_downloads = 0
        for i, track in enumerate(tracks):
            tr_title = track.track.to_dict()['title']
            tr_artist = track.track.to_dict()['artists'][0]['name']
            tr_title = tr_title.replace("/", "\\")
            track_name = f"{tr_title} - {tr_artist}"
            if track_name + ".mp3" in os.listdir(os.getcwd()):
                continue
            print(f"{tr_title} - {tr_artist}")
            track.track.download(f"./{tr_title} - {tr_artist}.mp3")
            num_of_downloads += 1
            # if i == 10:
            #     break
        if num_of_downloads == 0:
            print("You already have all tracks")
        else:
            print(f"Downloaded: {i} tracks")

    # def print_liked_tracks(self):
    #     tracks = self.client.users_likes_tracks()
    #     print("\n\n")
    #     for i, track in enumerate(tracks):
    #         tr_title = track.track.to_dict()['title']
    #         tr_artist = track.track.to_dict()['artists'][0]['name']
    #         tr_title = tr_title.replace("/", "\\")
    #         print(f"{tr_title} - {tr_artist}")
    #         self.liked_tracks_dict[i] = {f"{tr_title} - {tr_artist}"}
    #         # track.track.download(f"./tr/{tr_title} - {tr_artist}.mp3")
    #     print(f"You have {i} liked tracks")

    def download_track(self, track_id):
        # tracks = self.client.users_likes_tracks()
        tracks = self.tracks
        # os.chdir(os.path.join(os.getcwd(), 'cache'))
        # path = os.path.join(os.getcwd(), '/cache')
        path = os.getcwd() + "/music/"

        # if os.path.exists(os.path.join(path, 'cache')) is False:
        #     os.mkdir('cache')

        if self.liked_tracks_dict[track_id]+".mp3" in os.listdir(path):
            print("You already have this track")
            return
        track_short_info = tracks.tracks[int(track_id)]
        track_title = track_short_info.track.title.replace("/", "\\")
        track_short_info.track.download(
            f"./music/{track_short_info.track.artists[0]['name']} - {track_title}.mp3")
        track_short_info.track.download_og_image(
            f"./covers/{track_short_info.track.artists[0]['name']} - {track_title}.png")
        # for i, track in enumer22ate(tracks):
        #     tr_title = track.track.to_dict()['title']
        #     tr_artist = track.track.to_dict()['artists'][0]['name']
        #     # tr_title = tr_title.replace("/", "\\")
        #     # print(f"{tr_title} - {tr_artist}")
        #     track_name = f"{tr_title} - {tr_artist}"
        #     print(track_name, self.liked_tracks_dict[track_id])
        #     if track_name == self.liked_tracks_dict[track_id]:
        #         track.track.download(self.liked_tracks_dict[track_id] + ".mp3")
        #         return

    def update_liked_tracks(self):
        tracks = self.client.users_likes_tracks()
        self.liked_tracks_dict = OrderedDict()
        print("\n\n")
        for i, track in enumerate(tracks):
            # pprint(track.track.to_dict())
            # print(type(track))
            # print(track.track_id)
            # if i == 1:
            #     return
            tr_title = track.track.to_dict()['title']
            tr_artist = track.track.to_dict()['artists'][0]['name']
            tr_title = tr_title.replace("/", "\\")
            # print(f"{tr_title} - {tr_artist}")
            self.liked_tracks_dict[f"{i}"] = f"{tr_artist} - {tr_title}"
            self.liked_tracks_list.append(f"{tr_artist} - {tr_title}")

        with open('tracks.json', 'w') as fp:
            json.dump(self.liked_tracks_dict, fp,
                      indent=4, sort_keys=False)

    def delete_cached_tracks(self):
        print(os.listdir(os.getcwd()+"/music/"))
        path = os.getcwd()
        os.chdir(path+"/music")
        for i in os.listdir(os.getcwd()):
            if ".mp3" in i:
                os.remove(i)
        os.chdir("..")
        os.chdir(path+"/covers")
        for i in os.listdir(os.getcwd()):
            if ".png" in i:
                os.remove(i)
        os.chdir("..")
        for i in os.listdir(os.getcwd()):
            if ".mp3" in i:
                os.remove(i)
            if ".png" in i:
                os.remove(i)

    @staticmethod
    def login():
        print("Enter your email and password")
        email = input("Email:")
        password = input("Password:")

        client1 = Client.fromCredentials(email, password)
        settings_dict = {}
        settings_dict["TOKEN"] = client1.token
        main_TOKEN = client1.token
        with open('settings.json', 'w') as fp:
            json.dump(settings_dict, fp)
        isLoggedIn = True
        if os.path.exists('tracks.json'):
            os.remove('tracks.json')
        return main_TOKEN
        client1 = Ya_Client(main_TOKEN)

    @staticmethod
    def login_V2(email, password):
        client1 = Client.fromCredentials(email, password)
        settings_dict = {}
        settings_dict["TOKEN"] = client1.token
        main_TOKEN = client1.token
        with open('settings.json', 'w') as fp:
            json.dump(settings_dict, fp)
        isLoggedIn = True
        if os.path.exists('tracks.json'):
            os.remove('tracks.json')
        return main_TOKEN


# client1.print_liked_tracks()
# client1.update_liked_tracks()
# pprint(client1.liked_tracks_dict)

    # def save_liked_tracks_to_json(self):
    #     with open('tracks.json', 'w') as fp:
    #         json.dump(self.liked_tracks_dict, fp)
if __name__ == "__main__":
    # client1 = Ya_Client("email", "password")
    # test_TOKEN = "AgAAAABA_JRxAAG8Xj5hJ-A7AkQ6pYnHQTa1mew"
    # settings_dict = {}
    isLoggedIn = False
    client1 = None
    while isLoggedIn is not True:
        print("1:Use cur account\n2:New account")
        ans = input()

        if ans == "1":
            main_TOKEN = ''
            if os.path.exists('settings.json') is False:
                print("You are not Logged In")
                continue
            else:
                with open('settings.json', 'r') as fp:
                    main_TOKEN = json.load(fp)['TOKEN']
            isLoggedIn = True
            client1 = Ya_Client(main_TOKEN)
        elif ans == "2":
            try:
                main_TOKEN = Ya_Client.login()
            except yandex_music.exceptions.BadRequest as e:
                continue
            client1 = Ya_Client(main_TOKEN)
            isLoggedIn = True

    # pprint(client1.client.account_settings())
    # print(client1.client.token)

    # track = client1.client.tracks("7671:84228")
    # track = Track("84228:7671")
    # pprint(client1.tracks)

    # print(track.track_id)
    # pprint(track.get_download_info())
    # print(track)
    # print(track)
    # client1.update_liked_tracks()
    # client1.save_liked_tracks_to_json()

    # while True:
    #     os.system('clear')
    #     acc_info = client1.client.me
    #     print("Full Name:", acc_info.account.full_name)
    #     # acc_info.account.download_avatar('icon')
    #     print("1:Update Track List\n2:Download Track\n3:Download All Tracks\n4:Delete Cache Tracks")
    #     try:
    #         ans = int(input())
    #     except ValueError:
    #         continue
    #     if ans == 1:
    #         client1.update_liked_tracks()
    #         print("Tracks list:")
    #         for key, values in client1.liked_tracks_dict.items():
    #             pprint(values)
    #     elif ans == 2:
    #         print("Which track download?")
    #         pprint(client1.liked_tracks_dict)
    #         ans = input()
    #         client1.download_track(ans)
    #     elif ans == 3:
    #         print("Download to:\n1:Same dir\n2:New dir")
    #         ans = int(input())
    #         if ans == 1:
    #             client1.download_liked_tracks()
    #         elif ans == 2:
    #             print("Enter new dir name: ")
    #             dir_name = str(input())
    #             client1.download_liked_tracks(dir_name)
    #     elif ans == 4:
    #         client1.delete_cached_tracks()
    # pprint(client1.client.genres()[0]['title'])
    # for i in client1.client.genres():
    #     pprint(i['title'])

    # search = client1.client.search("Metallica")
    # pprint(search.best['result']['name'])
    # pprint(search.albums['results'][0])
    # for i in search.albums['results']:
    #     print(i['title'], i['year'],i['artists'][0]['name'])
    acc_info = client1.client.me
    print("Full Name:", acc_info.account.full_name)
    print(acc_info.account.region)
    # acc_info.account.registered_at
    # play1 = yandex_music.GeneratedPlaylist("playlistOfTheDay",client=client1)
    play2 = client1.client.users_playlists_list()
    # print(play2)
    # for i in play2:
    #     print(i['title'])
    feed = client1.client.feed()
    # print(feed.generated_playlists[0]['data']['title'])
    for i in feed.generated_playlists:
        print(i['data']['title'])
