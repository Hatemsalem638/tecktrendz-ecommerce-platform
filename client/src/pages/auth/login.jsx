import CommonForm from "@/components/common/form";
import { useToast } from "@/components/ui/use-toast";
import { loginFormControls } from "@/config";
import { loginUser, loginAsGuest } from "@/store/auth-slice";
import { useState } from "react";
import { useDispatch } from "react-redux";
import { Link } from "react-router-dom";


const initialState = {
  email: "",
  password: "",
};

function AuthLogin() {
  const [formData, setFormData] = useState(initialState);
  const dispatch = useDispatch();
  const { toast } = useToast();

  function onSubmit(event) {
    event.preventDefault();

    dispatch(loginUser(formData)).then((data) => {
      if (data?.payload?.success) {
        toast({
          title: data?.payload?.message,
        });
      } else {
        toast({
          title: data?.payload?.message,
          variant: "destructive",
        });
      }
    });
  }

  function handleGuestLogin() {
    dispatch(loginAsGuest()).then((data) => {
      if (data?.payload?.success) {
        toast({
          title: "Signed in as guest",
        });
      } else {
        toast({
          title: "Failed to sign in as guest",
          variant: "destructive",
        });
      }
    });
  }

  return (
    <div className="mx-auto w-full max-w-md space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Sign in to your account
        </h1>
        <p className="mt-2">
          Don't have an account
          <Link
            className="font-medium ml-2 text-primary hover:underline"
            to="/auth/register"
          >
            Register
          </Link>
        </p>
      </div>
      <CommonForm
        formControls={loginFormControls}
        buttonText={"Sign In"}
        formData={formData}
        setFormData={setFormData}
        onSubmit={onSubmit}
      />
      <div className="text-center">
        <button
          onClick={handleGuestLogin}
          className="text-sm text-blue-600 hover:underline mt-4"
        >
          Continue as Guest
        </button>
      </div>
      <div>
        <p className="text-sm mt-4">
          <a href="/auth/forgot-password" className="text-primary hover:underline">
            Forgot your password?
          </a>
        </p>
      </div>
                

    </div>
  );
}

export default AuthLogin;
