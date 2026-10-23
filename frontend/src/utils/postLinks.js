export function isExternalVideoPost(post) {
  return post?.post_type === 'video' && Boolean(post.video_url)
}

export function postHref(post, fallbackPath) {
  return isExternalVideoPost(post) ? post.video_url : fallbackPath
}

export function postTarget(post) {
  return isExternalVideoPost(post) ? '_blank' : undefined
}

export function postRel(post) {
  return isExternalVideoPost(post) ? 'noreferrer' : undefined
}
