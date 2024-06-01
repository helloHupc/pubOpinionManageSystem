export interface LoginForm {
    username: string
    password: string
}

export class LoginData {
    ruleForm: LoginForm = {
        username: "",
        password: ""
    }
}