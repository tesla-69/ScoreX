import mongoose from 'mongoose';

export const getGridFS = () => {
    if (!mongoose.connection || !mongoose.connection.db) {
        throw new Error('Database not connected');
    }
    return new mongoose.mongo.GridFSBucket(mongoose.connection.db, {
        bucketName: 'uploads'
    });
};