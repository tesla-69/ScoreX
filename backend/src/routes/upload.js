import express from "express";
import multer from "multer";
import { uploadFile } from "../services/fileUploadService.js";
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
});

const runScript = () => {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '..', '..', 'script', 'script.py');
    const pythonProcess = spawn('python', [scriptPath]);

    pythonProcess.stdout.on('data', (data) => {
      console.log(`Script output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Script error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Script exited with code ${code}`));
      }
    });
  });
};

router.post(
  "/upload",
  upload.fields([
    { name: "resumes", maxCount: 10 },
    { name: "jd", maxCount: 1 },
  ]),
  async (req, res) => {
    try {
      const resumes = req.files["resumes"];
      const jd = req.files["jd"]?.[0];
      const uploadResults = [];

      // Upload resumes
      if (resumes) {
        for (let file of resumes) {
          const result = await uploadFile(file, "resume");
          uploadResults.push(result);
        }
      }

      // Upload JD
      if (jd) {
        const result = await uploadFile(jd, "jd");
        uploadResults.push(result);
      }

      // Run the script after successful upload
      try {
        await runScript();
        res.status(200).json({
          message: "File upload complete and processing started",
          results: uploadResults,
        });
      } catch (scriptError) {
        console.error("Script execution error:", scriptError);
        res.status(200).json({
          message: "Files uploaded but processing failed",
          results: uploadResults,
          error: scriptError.message
        });
      }
    } catch (err) {
      console.error("Upload error:", err);
      res.status(500).json({
        error: "File upload failed",
        message: err.message,
      });
    }
  }
);

export default router;
