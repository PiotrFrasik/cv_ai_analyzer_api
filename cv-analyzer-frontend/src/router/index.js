import { createRouter, createWebHashHistory } from "vue-router";
import LoginForm from "@/views/LoginForm.vue";
import RegisterForm from "@/views/RegisterForm.vue";

const routes = [
    { path: '/login', component: LoginForm },
    { path: '/register', component: RegisterForm },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router