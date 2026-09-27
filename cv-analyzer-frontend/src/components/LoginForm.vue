<script setup>
import { ref } from 'vue'
import api from '../services/api'

const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
    errorMessage.value = ''
    try {
        const response = await api.post('/token/', {
            username: username.value,
            password: password.value,
        })
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        alert('Login successful!')
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
        <button type="submit">Sing in</button>
        <p v-if="errorMessage">{{ errorMessage }}</p>
    </form>
</template>