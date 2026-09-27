<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const profile = ref(null)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const response = await api.get('/user/profile/')
    profile.value = response.data
  } catch (error) {
    errorMessage.value = 'The profile could not be downloaded'
  }
})
</script>

<template>
  <h1>My Profile</h1>

  <p v-if="errorMessage">{{ errorMessage }}</p>

  <div v-if="profile">
    <p><strong>Username:</strong> {{ profile.username }}</p>
    <p><strong>Email:</strong> {{ profile.email }}</p>
    <p><strong>Phone:</strong> {{ profile.phone_number }}</p>

    <div v-if="profile.candidate_profile">
      <h2>Candidate Profile</h2>
      <p>Preferred department: {{ profile.candidate_profile.preferred_department }}</p>
    </div>

    <div v-if="profile.recruiter_profile">
      <h2>Recruiter Profile</h2>
      <p>Department: {{ profile.recruiter_profile.department }}</p>
    </div>
  </div>
</template>