import os
import logging

from satfetcher import app

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    app.run(port=os.getenv('PORT', 8080),
            host='0.0.0.0',
            debug=os.getenv('DEBUG'))
else:
    # make flask use gunicorn logger
    # https://stackoverflow.com/a/53555843
    logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
