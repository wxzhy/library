<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { useForm, useFormRules } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchUpdateBook, fetchCreateBook, fetchGetCategoryList } from '@/service/api';

defineOptions({ name: 'BookOperateDrawer' });

interface Props {
  /** the type of operation */
  operateType: UI.TableOperateType;
  /** the edit row data */
  rowData?: any | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => {
  const titles: Record<UI.TableOperateType, string> = {
    add: '添加图书',
    edit: '编辑图书'
  };
  return titles[props.operateType];
});

interface BookModel {
  title: string;
  author: string;
  isbn: string;
  publisher: string;
  publish_date: string;
  category: string;
  price: number | undefined;
  stock_quantity: number | undefined;
  description: string;
}

const model = ref(createDefaultModel());
const categories = ref<string[]>([]);

function createDefaultModel(): BookModel {
  return {
    title: '',
    author: '',
    isbn: '',
    publisher: '',
    publish_date: '',
    category: '',
    price: undefined,
    stock_quantity: undefined,
    description: ''
  };
}

const rules: Record<string, App.Global.FormRule> = {
  title: defaultRequiredRule,
  author: defaultRequiredRule,
  isbn: defaultRequiredRule,
  publisher: defaultRequiredRule,
  publish_date: defaultRequiredRule,
  category: defaultRequiredRule,
  price: defaultRequiredRule,
  stock_quantity: defaultRequiredRule
};

async function loadCategories() {
  try {
    const response = await fetchGetCategoryList();
    categories.value = response.data.categories || [];
  } catch (error) {
    console.error('Failed to load categories:', error);
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, props.rowData);
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  try {
    if (props.operateType === 'add') {
      await fetchCreateBook(model.value);
      window.$message?.success('图书添加成功');
    } else {
      await fetchUpdateBook(props.rowData.id, model.value);
      window.$message?.success('图书更新成功');
    }

    closeDrawer();
    emit('submitted');
  } catch (error) {
    window.$message?.error(`操作失败: ${error.message || error}`);
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
  }
});

onMounted(() => {
  loadCategories();
});
</script>

<template>
  <ElDrawer v-model="visible" :title="title" :size="480">
    <ElForm ref="formRef" :model="model" :rules="rules" label-position="top">
      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="书名" prop="title">
            <ElInput v-model="model.title" placeholder="请输入书名" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="作者" prop="author">
            <ElInput v-model="model.author" placeholder="请输入作者姓名" />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="ISBN" prop="isbn">
            <ElInput v-model="model.isbn" placeholder="请输入ISBN" />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="出版社" prop="publisher">
            <ElInput v-model="model.publisher" placeholder="请输入出版社" />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="出版日期" prop="publish_date">
            <ElDatePicker
              v-model="model.publish_date"
              type="date"
              placeholder="请选择出版日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="分类" prop="category">
            <ElSelect v-model="model.category" placeholder="请选择或输入分类" filterable allow-create>
              <ElOption
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
              />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="价格" prop="price">
            <ElInputNumber
              v-model="model.price"
              :min="0"
              :precision="2"
              placeholder="请输入价格"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="库存数量" prop="stock_quantity">
            <ElInputNumber
              v-model="model.stock_quantity"
              :min="0"
              placeholder="请输入库存数量"
              style="width: 100%"
            />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElFormItem label="描述" prop="description">
        <ElInput
          v-model="model.description"
          type="textarea"
          :rows="3"
          placeholder="请输入图书描述"
        />
      </ElFormItem>
    </ElForm>

    <template #footer>
      <ElSpace :size="16">
        <ElButton @click="closeDrawer">{{ $t('common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</ElButton>
      </ElSpace>
    </template>
  </ElDrawer>
</template>

<style scoped></style>
