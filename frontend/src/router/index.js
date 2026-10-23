import { createRouter, createWebHistory } from 'vue-router'
import { site } from '../config/site'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { title: 'About' },
  },
  // CTF 板块
  {
    path: '/ctf',
    name: 'CtfList',
    component: () => import('../views/ctf/CtfList.vue'),
    meta: { title: 'Articles' },
  },
  {
    path: '/ctf/:slug',
    name: 'CtfDetail',
    component: () => import('../views/ctf/CtfDetail.vue'),
    meta: { title: 'Articles' },
  },
  // 剪辑板块
  {
    path: '/editing',
    name: 'EditingList',
    component: () => import('../views/editing/EditingList.vue'),
    meta: { title: 'Projects' },
  },
  {
    path: '/editing/:slug',
    name: 'EditingDetail',
    component: () => import('../views/editing/EditingDetail.vue'),
    meta: { title: 'Projects' },
  },
  // 游戏板块
  {
    path: '/games',
    name: 'GamesList',
    component: () => import('../views/games/GamesList.vue'),
    meta: { title: 'Gallery' },
  },
  {
    path: '/games/:slug',
    name: 'GamesDetail',
    component: () => import('../views/games/GamesDetail.vue'),
    meta: { title: 'Gallery' },
  },
  // 404 兜底
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为: 切换页面时回到顶部
  scrollBehavior() {
    return { top: 0 }
  },
})

// 根据路由设置页面标题
router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · ${site.name}` : site.name
})

export default router
