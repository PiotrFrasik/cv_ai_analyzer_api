<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()

async function handleLogin() {
    errorMessage.value = ''
    try {
        const response = await api.post('/token/', {
            username: username.value,
            password: password.value,
        })
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        router.push('/profile')
    } catch (error) {
        errorMessage.value = "Wrong login or password"
    }
}
</script>

<template>
    <form @submit.prevent="handleLogin">
        <div>
            <label>Username:</label>
            <input v-model="username" type="text" />
        </div>
        <div>
            <label>Password:</label>
            <input v-model="password" type="password" />
        </div>
        <button type="submit">Sign in</button>
        <p v-if="errorMessage">{{ errorMessage }}</p>
    </form>
</template>