#!/usr/bin/env python3
"""Post microsemantic updates to Twitter."""

import logging
from typing import Optional

try:
    import tweepy  # type: ignore
except ImportError:  # pragma: no cover
    tweepy = None


def post_update(message: str, creds: Optional[dict] = None) -> None:
    if not tweepy:
        logging.warning("tweepy not installed; cannot post: %s", message)
        return
    if not creds:
        logging.error("No Twitter credentials provided")
        return
    auth = tweepy.OAuth1UserHandler(
        creds["api_key"], creds["api_secret"], creds["access_token"], creds["access_secret"],
    )
    api = tweepy.API(auth)
    api.update_status(message)
    logging.info("Tweeted: %s", message)

if __name__ == "__main__":
    post_update("Test tweet from SIOS")
