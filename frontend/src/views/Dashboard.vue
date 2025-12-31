<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Domain</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="company in companies" :key="company.id">
          <td>{{ company.id }}</td>
          <td>{{ company.name }}</td>
          <td>{{ company.domain }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';

const companies = ref([]);

onMounted(async () => {
  try {
    const response = await api.get('/companies/');
    companies.value = response.data;
  } catch (error) {
    console.error('Failed to fetch companies', error);
  }
});
</script>
