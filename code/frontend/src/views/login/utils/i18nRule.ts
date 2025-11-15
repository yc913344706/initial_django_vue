import { reactive } from "vue";
import type { FormRules } from "element-plus";
import { useI18n } from 'vue-i18n';

/** 密码正则（密码格式应为8-18位数字、字母、符号的任意两种组合） */
export const REGEXP_PWD =
  /^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?!([^(0-9a-zA-Z)]|[()])+$)(?!^.*[\u4E00-\u9FA5].*$)([^(0-9a-zA-Z)]|[()]|[a-z]|[A-Z]|[0-9]){8,18}$/;

/** 创建登录校验规则，支持国际化 */
export function createLoginRules() {
  const { t } = useI18n();
  
  const loginRules = reactive(<FormRules>{
    username: [
      {
        required: true,
        message: t('message.requiredUsername'),
        trigger: "blur"
      },
      {
        min: 1,
        max: 20,
        message: t('message.usernameLengthError'),
        trigger: "blur"
      }
    ],
    password: [
      {
        validator: (rule, value, callback) => {
          if (value === "") {
            callback(new Error(t('message.requiredPassword')));
          } else if (!REGEXP_PWD.test(value)) {
            callback(
              new Error(t('message.passwordFormatError'))
            );
          } else {
            callback();
          }
        },
        trigger: "blur"
      }
    ]
  });
  
  return loginRules;
}