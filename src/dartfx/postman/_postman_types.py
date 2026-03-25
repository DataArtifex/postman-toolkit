"""Helpers for narrowing typed postman collection models."""

from typing import cast

from dartfx.postmanapi import postman_collection


def ensure_collection_info(collection: postman_collection.Collection) -> postman_collection.Info:
    info = collection.info
    if info is None:
        info = postman_collection.Info()
        collection.info = info
    return info


def ensure_item_request(item: postman_collection.Item) -> postman_collection.Request:
    request = item.request
    if request is None:
        request = postman_collection.Request()
        item.request = request
    return request


def create_item_request(item: postman_collection.Item, url: str, method: str = "GET") -> postman_collection.Request:
    request = item.create_request(url, method)
    if request is None:
        raise TypeError("Item.create_request() returned None")
    return request


def ensure_request_url(request: postman_collection.Request) -> postman_collection.URL:
    url = request.url
    if isinstance(url, postman_collection.URL):
        return url
    if url is None:
        typed_url = postman_collection.URL()
        request.url = typed_url
        return typed_url
    raise TypeError("Expected request.url to be a URL instance")


def as_collection(resource: postman_collection.CollectionResource) -> postman_collection.Collection:
    return cast(postman_collection.Collection, resource)
