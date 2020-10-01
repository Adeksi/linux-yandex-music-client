from yandex_music.client import Client
import os
from pprint import pprint


class Ya_Client:
    def __init__(self, username, password):
        self.client = Client.from_credentials(username, password)
        self.liked_tracks_dict = {}
        self.tracks = self.client.users_likes_tracks()

    def download_liked_tracks(self, dir_name=None):
        tracks = self.client.users_likes_tracks()
        print("\n\n")
        print(dir_name)
        # i = 0

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
        path = os.getcwd()
        if self.liked_tracks_dict[track_id]+".mp3" in os.listdir(path):
            print("You already have this track")
            return
        for i, track in enumerate(tracks):
            tr_title = track.track.to_dict()['title']
            tr_artist = track.track.to_dict()['artists'][0]['name']
            tr_title = tr_title.replace("/", "\\")
            # print(f"{tr_title} - {tr_artist}")
            track_name = f"{tr_title} - {tr_artist}"
            print(track_name, self.liked_tracks_dict[track_id])
            if track_name == self.liked_tracks_dict[track_id]:
                track.track.download(self.liked_tracks_dict[track_id] + ".mp3")
                return

    def update_liked_tracks(self):
        tracks = self.client.users_likes_tracks()
        print("\n\n")
        for i, track in enumerate(tracks):
            tr_title = track.track.to_dict()['title']
            tr_artist = track.track.to_dict()['artists'][0]['name']
            tr_title = tr_title.replace("/", "\\")
            # print(f"{tr_title} - {tr_artist}")
            self.liked_tracks_dict[i] = f"{tr_title} - {tr_artist}"

    def delete_cached_tracks(self):
        for i in os.listdir(os.getcwd()):
            if ".mp3" in i:
                os.remove(i)


# client1.print_liked_tracks()
# client1.update_liked_tracks()
# pprint(client1.liked_tracks_dict)
if __name__ == "__main__":
    client1 = Ya_Client("email", "password")
    client1.update_liked_tracks()
    while True:
        print("1:Update Track List\n2:Download Track\n3:Download All Tracks\n4:Delete Cache Tracks")
        try:
            ans = int(input())
        except ValueError:
            continue
        if ans == 1:
            client1.update_liked_tracks()
            print("Tracks list:")
            for key, values in client1.liked_tracks_dict.items():
                pprint(values)
        elif ans == 2:
            print("Which track download?")
            pprint(client1.liked_tracks_dict)
            ans = int(input())
            client1.download_track(ans)
        elif ans == 3:
            print("Download to:\n1:Same dir\n2:New dir")
            ans = int(input())
            if ans == 1:
                client1.download_liked_tracks()
            elif ans == 2:
                print("Enter new dir name: ")
                dir_name = str(input())
                client1.download_liked_tracks(dir_name)
        elif ans == 4:
            client1.delete_cached_tracks()