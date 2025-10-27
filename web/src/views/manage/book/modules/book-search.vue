<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { $t } from '@/locales';
import { fetchGetCategoryList } from '@/service/api';

defineOptions({ name: 'BookSearch' });

const activeName = ref(['book-search']);

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

interface BookSearchParams {
  title?: string;
  author?: string;
  publisher?: string;
  category?: string;
  isbn?: string;
}

const model = defineModel<BookSearchParams>('model', { required: true });

const categories = ref<string[]>([]);

async function loadCategories() {
  try {
    const response = await fetchGetCategoryList();
    categories.value = response.data.categories || [];
  } catch (error) {
    console.error('Failed to load categories:', error);
  }
}

function reset() {
  emit('reset');
}

function search() {
  emit('search');
}

onMounted(() => {
  loadCategories();
});
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse v-model="activeName">
      <ElCollapseItem title="搜索条件" name="book-search">
        <ElForm :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="书名" prop="title">
                <ElInput v-model="model.title" placeholder="请输入书名" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="作者" prop="author">
                <ElInput v-model="model.author" placeholder="请输入作者姓名" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="出版社" prop="publisher">
                <ElInput v-model="model.publisher" placeholder="请输入出版社" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="分类" prop="category">
                <ElSelect v-model="model.category" placeholder="请选择分类" clearable filterable>
                  <ElOption
                    v-for="category in categories"
                    :key="category"
                    :label="category"
                    :value="category"
                  />
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="ISBN" prop="isbn">
                <ElInput v-model="model.isbn" placeholder="请输入ISBN" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="24" :md="24" :sm="24">
              <ElSpace class="w-full justify-end" alignment="end">
                <ElButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </ElButton>
                <ElButton type="primary" plain @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  {{ $t('common.search') }}
                </ElButton>
              </ElSpace>
            </ElCol>
          </ElRow>
        </ElForm>
      </ElCollapseItem>
    </ElCollapse>
  </ElCard>
</template>

<style scoped></style>
