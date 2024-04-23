# Telegram docx Reader Bot

It's a Telegram bot written in Python, using [Telepot API](https://github.com/nickoala/telepot), which can read docx files.

It receives a file written in docx format and answer the user with the ASCII content of this file.

## Official bot

The official bot is running in Heroku cloud server and can be found in https://t.me/docxReader_bot .

To try it, just send him a message.

## Content

  This path should contain those files and subdirs:

    docx2txt.py     ===> module to extract ASCII data from docx file;
    docxbot.py      ===> main bot module;
    testFile.docx   ===> a .docx file that can be used to test the bot;
    temp/           ===> a subdir to stock temporally files;
    token.txt       ===> a simple text file with a bot token;

## Usage

To run bot:
1. Fork or clone this repository
2. Get a bot token talking to [BotFather](https://t.me/BotFather)
3. Create a file token.txt in the project's root with your bot token written in it
4. Run bot: `python docxbot.py`

IMPORTANT:
The file token.txt shouldn't have spaces or line breaks. It might contain only your bot's token.
To know more about this go to [telegram bots documentation](https://core.telegram.org/bots#creating-a-new-bot)

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
