<script setup>
</script>

<template>
  <header>
    <nav>
      <RouterLink to="/login">Login</RouterLink> |
      <RouterLink to="/register">Register</RouterLink>
    </nav>
  </header>

  <main>
    <RouterView />
  </main>
</template>