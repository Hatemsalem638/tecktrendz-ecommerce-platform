import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import ShoppingHeader from "@/components/shopping-view/header";

function ClothTryon() {
  const { t } = useTranslation();
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/shop/products/get');
        const data = await response.json();
        if (data.success) {
          setProducts(data.data);
        } else {
          console.error('Failed to fetch products');
        }
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };

    fetchProducts();
  }, []);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async () => {
    if (!image || !selectedProduct) {
      alert(t("Please select both an image and a product."));
      return;
    }

    const formData = new FormData();
    formData.append('userImage', image);
    formData.append('productId', selectedProduct._id);

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/api/tryon', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setIsLoading(false);

      if (data.success && data.outputImage) {
        setOutputImage(`http://localhost:5000/tryon-results/tryon_result.jpg`);
      } else {
        alert(t("Try-on failed. Please check the console."));
        console.error(data);
      }
    } catch (error) {
      setIsLoading(false);
      console.error('Error:', error);
      alert(t("An error occurred while processing."));
    }
  };

  return (
    <>
      <ShoppingHeader />
      <div className="min-h-screen bg-background text-foreground p-6">
        <h1 className="text-3xl font-bold text-center mb-10">{t("Virtual Try-On")}</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">{t("Upload Your Image")}</label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="w-full bg-muted p-3 rounded"
              />
              {preview && (
                <img src={preview} alt="Preview" className="mt-4 rounded shadow max-h-[400px]" />
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{t("Select a Product")}</label>
              <div className="max-h-64 overflow-y-auto border border-muted rounded bg-muted/30">
                {products.map((product) => (
                  <div
                    key={product._id}
                    className={`flex items-center gap-4 p-3 cursor-pointer hover:bg-muted/50 transition 
                    ${selectedProduct?._id === product._id ? "bg-primary/10" : ""}`}
                    onClick={() => setSelectedProduct(product)}
                  >
                    <img
                      src={product.image}
                      alt={product.title}
                      className="w-14 h-14 object-cover rounded"
                    />
                    <span className="text-sm font-medium">{product.title}</span>
                  </div>
                ))}
                {products.length === 0 && (
                  <div className="text-center p-2 text-muted-foreground">{t("Loading products...")}</div>
                )}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={isLoading || !image || !selectedProduct}
              className={`w-full p-3 rounded text-white font-semibold transition 
                ${isLoading || !image || !selectedProduct
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : 'bg-primary hover:bg-primary/80'}`}
            >
              {isLoading ? t("Processing...") : t("Try On")}
            </button>
          </div>

          <div className="flex flex-col items-center justify-start">
            {outputImage ? (
              <>
                <h3 className="text-xl font-semibold mb-4">{t("Try-On Result")}</h3>
                <img src={outputImage} alt="Try-On Output" className="rounded shadow max-w-full max-h-[500px]" />
              </>
            ) : (
              <div className="text-muted-foreground text-center italic">
                {t("Upload an image and select a product to preview the try-on result.")}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default ClothTryon;
