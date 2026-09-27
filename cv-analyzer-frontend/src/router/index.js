import { createRouter, createWebHashHistory } from "vue-router";
import LoginForm from "@/views/LoginForm.vue";
import RegisterForm from "@/views/RegisterForm.vue";
import ProfileView from "@/views/ProfileView.vue";

const routes = [
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
    { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

// global guardian
router.beforeEach((to, form, next) => {
    const isLoggedIn = !!localStorage.getItem('access_token')

    if (to.meta.requiresAuth && !isLoggedIn) {
        next('/login') 
    } else {
        next()
    }
})

export default router