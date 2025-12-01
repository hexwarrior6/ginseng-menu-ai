<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header class="header" style="background: #fff; padding: 0; display: flex; align-items: center;">
      <div class="logo" style="padding: 0 20px; font-size: 18px; font-weight: bold;">Ginseng Menu AI Admin Panel</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="horizontal"
        :style="{ flex: 1, justifyContent: 'center' }"
      >
        <a-menu-item key="dashboard">
          <router-link to="/">Dashboard</router-link>
        </a-menu-item>
        <a-menu-item key="users">
          <router-link to="/users">Users</router-link>
        </a-menu-item>
        <a-menu-item key="dishes">
          <router-link to="/dishes">Dishes</router-link>
        </a-menu-item>
        <a-menu-item key="user-dishes">
          <router-link to="/user-dishes">User Dishes</router-link>
        </a-menu-item>
        <a-menu-item key="logs">
          <router-link to="/logs">Interaction Logs</router-link>
        </a-menu-item>
      </a-menu>
    </a-layout-header>
    <a-layout-content style="padding: 24px;">
      <div :style="{ background: '#fff', padding: '24px', minHeight: '360px' }">
        <router-view />
      </div>
    </a-layout-content>
    <a-layout-footer style="text-align: center;">
      Ginseng Menu AI Admin Panel ©{{ new Date().getFullYear() }}
    </a-layout-footer>
  </a-layout>
</template>

<script>
export default {
  name: 'MainLayout',
  data() {
    return {
      selectedKeys: ['dashboard'],
    };
  },
  watch: {
    $route(to) {
      // Update selected menu item based on current route
      if (to.path === '/') {
        this.selectedKeys = ['dashboard'];
      } else if (to.path.startsWith('/users')) {
        this.selectedKeys = ['users'];
      } else if (to.path.startsWith('/dishes')) {
        this.selectedKeys = ['dishes'];
      } else if (to.path.startsWith('/logs')) {
        this.selectedKeys = ['logs'];
      } else if (to.path.startsWith('/user-dishes')) {
        this.selectedKeys = ['user-dishes'];
      }
    }
  },
  mounted() {
    // Set initial selected key based on current route
    if (this.$route.path === '/') {
      this.selectedKeys = ['dashboard'];
    } else if (this.$route.path.startsWith('/users')) {
      this.selectedKeys = ['users'];
    } else if (this.$route.path.startsWith('/dishes')) {
      this.selectedKeys = ['dishes'];
    } else if (this.$route.path.startsWith('/logs')) {
      this.selectedKeys = ['logs'];
    } else if (this.$route.path.startsWith('/user-dishes')) {
      this.selectedKeys = ['user-dishes'];
    }
  }
};
</script>
