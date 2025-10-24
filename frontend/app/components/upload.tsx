import { useState } from "react";
import Chat from "./chat";
export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isUploaded, setIsUploaded] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected && selected.type === "application/pdf") {
      setFile(selected);
      setPdfUrl(URL.createObjectURL(selected));
      uploadPdf(selected);
      setIsUploaded(true);
    }
  };

  const uploadPdf = async (pdf: File) => {
    const formData = new FormData();
    formData.append("file", pdf);

    const res = await fetch("http://127.0.0.1:8000/ingest_pdf", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    console.log("Upload response:", data);
  };

  return (
    <>
      {!isUploaded ? (
        <div className="flex justify-center mt-10 gap-6">
          <div className="w-1/2">
            <label className="cursor-pointer flex flex-col items-center justify-center border-2 border-dashed border-blue-400 p-10 rounded-lg bg-gradient-to-r from-blue-300 to-purple-300 opacity-80 hover:opacity-100 transition">
              <span className="text-5xl text-blue-400 bg-white w-16 h-16 flex items-center justify-center rounded-full border shadow-lg mb-4">
                +
              </span>
              <h1 className="text-xl font-bold text-blue-700">
                Upload your document
              </h1>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                hidden
              />
            </label>
          </div>
        </div>
      ) : (
        <div className="flex mt-20 mr-10 ml-10 gap-4">
          <div className=" w-3/4 h-[90vh] flex-1">
            <iframe
              src={pdfUrl || undefined}
              className="w-full h-full border rounded-lg"
              title="PDF Preview"
            />
          </div>
          <div className="flex-2">
            <Chat />
          </div>
        </div>
      )}
    </>
  );
}
