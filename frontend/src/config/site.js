// Public branding. Content, categories and About text are editable in Django admin.
export const site = {
  name: import.meta.env.VITE_SITE_NAME || 'Eclipse',
  heroTitle: import.meta.env.VITE_HERO_TITLE || 'Your Space',
  slogan: import.meta.env.VITE_SITE_SLOGAN || '从这里开始，写下你的故事。',
  icpNumber: import.meta.env.VITE_ICP_NUMBER || '',
  aboutVideo: import.meta.env.VITE_ABOUT_VIDEO || '/wallpaper/aboutme.mp4',
  gamesVideo: import.meta.env.VITE_GAMES_VIDEO || '/wallpaper/elden-ring-wallpaper.mp4',
}
