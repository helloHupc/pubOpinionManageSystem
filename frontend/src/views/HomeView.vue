<template>
  <div>
    <h1>Home</h1>
    <p>Welcome to the home page!</p>
  </div>
  <button @click="handleLogout">Logout</button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'Home',
  setup() {
    const router = useRouter();

    const handleLogout = () => {
      localStorage.removeItem('token');
      router.push({ name: 'Login' });
    };

    return {
      handleLogout,
    };
  },
});
</script>
