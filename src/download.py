"""Download the PHYLACINE trait data into the data/ folder."""

import os
import requests

URL = (
    "https://raw.githubusercontent.com/MegaPast2Future/PHYLACINE_1.2/"
    "refs/heads/master/Data/Traits/Trait_data.csv"
)
FILE_PATH = "data/Trait_data.csv"


def download_traits():
    """Download Trait_data.csv into the data/ folder, unless it is already there.

    Returns
    -------
    str
        The path of the CSV file.

    Raises
    ------
    RuntimeError
        If the download fails.
    """
    if os.path.exists(FILE_PATH):
        print("The file is already there, nothing to download.")
        return FILE_PATH

    # creates the data folder. exist_ok=True prevents a FileExistsError if it already exists
    os.makedirs("data", exist_ok=True)

    # error handling:
    try:
        # downloads the file but gives up if it takes more than 30 seconds
        # calling requests.get(URL) sends an HTTP request to the server
        # the response is assigned to the variable "response"
        # response holds several attributes such as .content and .status_code
        response = requests.get(URL, timeout=30)

        # checks the server's answer for 404 (not found) or 403 (forbidden)
        response.raise_for_status()

    # catches any download problems such as: no internet, timeout, bad answer
    except requests.RequestException as error:

        # tells the user what to do in case of an error
        raise RuntimeError(
            "Download failed. Please download Trait_data.csv manually from Github "
            "(https://raw.githubusercontent.com/MegaPast2Future/"
            "PHYLACINE_1.2/refs/heads/master/Data/Traits/Trait_data.csv) "
            "and put it in the data/ folder."
        ) from error

    # opens the file for writing in binary mode because .content is in bytes
    # "with" guarantees that the file gets closed even if there is an error inside
    # "wb" rather than "w" to avoid unnecessary decoding and encoding
    with open(FILE_PATH, "wb") as file:
        file.write(response.content)

    print("Download complete:", FILE_PATH)
    return FILE_PATH


# runs only when this file is executed directly, not when it is imported.
# because the name is "src.download" (module name) when it is imported
if __name__ == "__main__":
    download_traits()
