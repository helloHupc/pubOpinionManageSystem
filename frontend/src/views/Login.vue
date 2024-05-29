<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axiosInstance from '../axiosConfig';

export default defineComponent({
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axiosInstance.post('/login', {
          username: this.username,
          password: this.password,
        });
        console.log('Login successful:', response.data);
        // handle success (e.g., store token, redirect)
      } catch (error) {
        console.error('Login failed:', error);
        // handle error (e.g., show error message)
      }
    },
  },
});
</script>

<style scoped>
/* 添加你的样式 */
</style>
