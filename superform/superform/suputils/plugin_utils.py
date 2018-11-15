import re


def post_pre_validation_plugins(post, maxLengthTitle, maxLengthDescription):
    pattern = '^(?:(?:https?|http?|wwww?):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$';
    if len(post.title) > maxLengthTitle or len(post.title) == 0: return 0
    if len(post.description) > maxLengthDescription or len(post.description) == 0: return 0
    if not (post.link_url is None) or (len(post.link_url)) > 0:
        if re.match(pattern, post.link_url, 0) is None: return 0
    print("img link",type(post.image_url))
    if not (post.image_url is None) or (len(post.image_url) > 0):
        if re.match(pattern, post.image_url, 0) is None: return 0
    return 1
