# LuluAPI
A python library that utilizes Lulu's print API to facilitate communication between a developer and Lulu. It uses all of the available features that Lulu provides on their documentation page, and converts them into easy-to-use Python functions. All of the inputs and outputs are dictionaries, converting Lulu's JSON messages into something that is ready to use for any Python developer.

## Getting Started
In order to use the Lulu API, you need a set of keys to faciliate communication. If you have a Lulu developer account, they keys can be found [here](https://developers.lulu.com/user-profile/api-keys). Additionally, if you wish to run tests, you will need a seperate set of sandbox keys, found [here](https://developers.sandbox.lulu.com/user-profile/api-keys). Once you have your keys, you should place them in their respective spots in the lulu_token.py file. Ensure that the sandbox keys and the non-sandbox keys are in the correct locations to avoid accidentally sending real print-jobs to Lulu during testing.

"""python
if SANDBOX:
    print("***SANDBOX ACTIVE***")
    URLPREFIX = "https://api.sandbox.lulu.com/"

    """SANDBOX CLIENT KEYS"""

    CLIENT_KEY = "PLACE SANDBOX KEY HERE"

    CLIENT_SECRET = "PLACE SANDBOX KEY HERE"

    BASE64_KEY_SECRET = "PLACE SANDBOX KEY HERE, INCLUDING basic"

else:
    URLPREFIX = f"https://api.lulu.com/"

    """CLIENT KEYS"""
    CLIENT_KEY = "PLACE KEY HERE"

    # The client secret can be changed on the developer tools website.
    CLIENT_SECRET = "PLACE KEY HERE"

    # This is the combined key in base 64. The word "basic" is required prior to the rest of the code.
    BASE64_KEY_SECRET = "PLACE KEY HERE, INCLUDING basic"
"""

## Documentation
All of the documentation for the functions is included in the request.py file.

## Simple API
Some of the functions in the original API have complicated inputs and outputs. To alleviate this, some of the functions that deal with creating and managing print-jobs have a "simple" version, which is also documented. This allows you to send and recieve a singular dictionary to Lulu, rather than needing to manage the changing data structures yourself.

## Contributing
Pull requests are welcome. If you notice an error during your implementation, open an issue to highlight the problem first.
