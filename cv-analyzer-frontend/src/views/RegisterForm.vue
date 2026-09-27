<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const username = ref('')
const password = ref('')
const phone_number = ref('')
const email = ref('')
const errorMessage = ref('')
const router = useRouter()

async function handleRegister() {
    errorMessage.value = ''
    try {
        const response = await api.post('/user/register/', {
            username: username.value,
            password: password.value,
            phone_number: phone_number.value,
            email: email.value,
        })
        router.push('/login')
    } catch (error) {
        errorMessage.value = "Registration failed. Please check your data and try again."
    }
}

</script>

<template>
    <form @submit.prevent="handleRegister">
        <div>
            <label>Username:</label>
            <input v-model="username" type="text" />
        </div>
        <div>
            <label>Password:</label>
            <input v-model="password" type="password" />
        </div>
        <div>
            <label>Phone number:</label>
            <input v-model="phone_number" type="text" />
        </div>
        <div>
            <label>Email:</label>
            <input v-model="email" type="text" />
        </div>
        <button type="submit">Register now</button>
        <p v-if="errorMessage">{{ errorMessage }}</p>
    </form>
</template>