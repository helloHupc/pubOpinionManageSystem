<template>
  <div>
    <LoginForm v-if="showLoginForm" @switch-to-register="showLoginForm = false" />
    <RegisterForm v-if="!showLoginForm" @switch-to-login="showLoginForm = true" />
  </div>
</template>

<script lang="ts">
import { LoginForm, RegisterForm } from './components'
import {defineComponent, ref} from "vue";

export default defineComponent({
  components: {
    LoginForm,
    RegisterForm
  },
  setup() {

    const showLoginForm = ref(true);

    return {
      showLoginForm,
    }
  },
});
</script>
