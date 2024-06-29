import service from "@/request/index";
interface loginData{
    username:string,
    password:string
}
export function login(data:loginData){
    return service({
        url:'/login',
        method:'post',
        data
    })
}

interface registerData{
    username:string,
    password1:string,
    password2:string,
}
export function register(data:registerData){
    return service({
        url:'/register',
        method:'post',
        data
    })
}