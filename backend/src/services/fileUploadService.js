import { getGridFS } from '../config/gridfs.js';

export const uploadFile = async (file, type) => {
    const gfsBucket = getGridFS();
    
    try {
        const uploadStream = gfsBucket.openUploadStream(file.originalname, {
            contentType: file.mimetype,
            metadata: {
                type,
                uploadDate: new Date()
            }
        });

        await new Promise((resolve, reject) => {
            uploadStream.end(file.buffer, (error) => {
                if (error) reject(error);
                else resolve();
            });
        });

        return {
            filename: file.originalname,
            status: 'success',
            id: uploadStream.id
        };
    } catch (error) {
        return {
            filename: file.originalname,
            status: 'failed',
            error: error.message
        };
    }
};