"""
Simple command-line interface to music service
"""

# Standard library modules
import argparse
import cmd
import re

# Installed packages
import requests
import jwt

# The services check only that we pass an authorization,
# not whether it's valid
# DEFAULT_AUTH = 'Bearer A'
# global DEFAULT_AUTH


def parse_args():
    argp = argparse.ArgumentParser(
        'mcli',
        description='Command-line query interface to music service'
        )
    argp.add_argument(
        'name',
        help="DNS name or IP address of music server"
        )
    argp.add_argument(
        'port',
        type=int,
        help="Port number of music server"
        )
    return argp.parse_args()


def get_url(name, port):
    return "http://{}:{}/api/v1/music/".format(name, port)

def get_s1_url(name, port):
    return "http://{}:{}/api/v1/user/".format(name, port)


def parse_quoted_strings(arg):
    """
    Parse a line that includes words and '-, and "-quoted strings.
    This is a simple parser that can be easily thrown off by odd
    arguments, such as entries with mismatched quotes.  It's good
    enough for simple use, parsing "-quoted names with apostrophes.
    """
    mre = re.compile(r'''(\w+)|'([^']*)'|"([^"]*)"''')
    args = mre.findall(arg)
    return [''.join(a) for a in args]


class Mcli(cmd.Cmd):
    def __init__(self, args):
        self.USER_ID = ""
        # DEFAULT_AUTH = ""
        self.name = args.name
        self.port = args.port
        cmd.Cmd.__init__(self)
        self.prompt = 'mql: '
        self.intro = """
Command-line interface to music service.
Enter 'help' for command list.
'Tab' character autocompletes commands.
"""

    def do_read(self, arg):
        """
        Read a single song or list all songs.

        Parameters
        ----------
        song:  music_id (optional)
            The music_id of the song to read. If not specified,
            all songs are listed.

        Examples
        --------
        read 6ecfafd0-8a35-4af6-a9e2-cbd79b3abeea
            Return "The Last Great American Dynasty".
        read
            Return all songs (if the server supports this).

        Notes
        -----
        Some versions of the server do not support listing
        all songs and will instead return an empty list if
        no parameter is provided.
        """
        # if DEFAULT_AUTH == "":
        #     print("no user logged in")
        #     return
        url = get_url(self.name, self.port)
        r = requests.get(
            url+arg.strip(),
            headers={'Authorization': self.USER_ID}
            )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)
        items = r.json()
        if 'Count' not in items:
            print("0 items returned")
            return
        print("{} items returned".format(items['Count']))
        for i in items['Items']:
            print("{}  {:20.20s} {}    owner: {}".format(
                i['music_id'],
                i['Artist'],
                i['SongTitle'],
                i['Owner']))

    def do_create(self, arg):
        """
        Add a song to the database.

        Parameters
        ----------
        artist: string
        title: string

        Both parameters can be quoted by either single or double quotes.

        Examples
        --------
        create 'Steely Dan'  "Everyone's Gone to the Movies"
            Quote the apostrophe with double-quotes.

        create Chumbawamba Tubthumping
            No quotes needed for single-word artist or title name.
        """
        if self.USER_ID == "":
            print("no user logged in")
            return
        url = get_url(self.name, self.port)
        args = parse_quoted_strings(arg)
        payload = {
            'Artist': args[0],
            'SongTitle': args[1],
            'Owner': self.USER_ID
        }
        r = requests.post(
            url,
            json=payload,
            headers={'Authorization': self.USER_ID}
        )
        print(r.json())

    def do_delete(self, arg):
        """
        Delete a song.

        Parameters
        ----------
        song: music_id
            The music_id of the song to delete.

        Examples
        --------
        delete 6ecfafd0-8a35-4af6-a9e2-cbd79b3abeea
            Delete "The Last Great American Dynasty".
        """
        if self.USER_ID == "":
            print("no user logged in")
            return
        url = get_url(self.name, self.port)
        r = requests.delete(
            url+arg.strip(),
            headers={'Authorization': self.USER_ID}
            )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)

    def do_quit(self, arg):
        """
        Quit the program.
        """
        return True

    def do_test(self, arg):
        """
        Run a test stub on the music server.
        """
        if self.USER_ID == "":
            print("no user logged in")
            return
        url = get_url(self.name, self.port)
        r = requests.get(
            url+'test',
            headers={'Authorization': self.USER_ID}
            )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)

    def do_shutdown(self, arg):
        """
        Tell the music cerver to shut down.
        """
        if DEFAULT_AUTH == "":
            print("no user logged in")
            return
        url = get_url(self.name, self.port)
        r = requests.get(
            url+'shutdown',
            headers={'Authorization': self.USER_ID}
            )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)

    # def do_wtf(self, arg):
    #     print("I dont know how the fuck work")

    def do_login(self, arg):
        if self.USER_ID != "":
            print("Already signed in as: " + self.USER_ID)
            return

        payload = {
            'uid': arg.strip(),
        }
        url = get_s1_url(self.name, self.port)
        r = requests.put(
            url+"login",
            json=payload,
           
        )
        print(url)
        # print(r.json())
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)
            return
        print("json:  " + r.text)
        decode = jwt.decode(r.text, 'secret', algorithms='HS256')
        print(decode)
        self.USER_ID = decode["user_id"]
        # self.USER_ID = self.USER_ID
        print(self.USER_ID)
        
    def do_create_user(self, arg):
        payload = {
            'fname': arg[0],
            'lname': arg[1],      
            'email': arg[2],           
        }
        url = get_s1_url(self.name, self.port)
        r = requests.post(
            url,
            json=payload,           
        )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)
        print(r.json())

    def do_logoff(self, arg):
        payload = {'jwt' : ""}
        url = get_s1_url(self.name, self.port)
        r = requests.put(
            url+"logoff",
            json=payload,           
        )
        if r.status_code != 200:
            print("Non-successful status code:", r.status_code)
            return
        print("log out" + self.USER_ID)
        self.USER_ID = ""
        # DEFAULT_AUTH = ""


if __name__ == '__main__':
    args = parse_args()
    Mcli(args).cmdloop()