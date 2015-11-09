import leveldb, argparse, numpy
from caffe.proto import caffe_pb2


class DummyTrainingInstance():
    """assumed interface of training instance"""
    def __init__(self):
        pass

    def getArray(self):
        channels = 1
        window_size = 5
        vector_size = 300
        dimensions = (channels, window_size, vector_size)

        array = numpy.zeros((dimensions))

        return array

    def getLabel(self):
        return 0

class CreateLevelDB():
    """create a new level db, fill it with word vectors"""
    def __init__(self, filename, batchsize = 1000):
        self.__filename = filename
        self.__db = leveldb.LevelDB(filename)
        self.__current_batch_size = 0
        self.__batch = None
        self.__index = 0
        self.batchsize = batchsize

    def writeTrainingInstanceList(self, training_instance_list):
        for training_instance in training_instance_list:
            self.writeTrainingInstance(training_instance)

    def writeTrainingInstance(self, training_instance):
        if (self.__batch == None):
            self.__batch = leveldb.WriteBatch()

        vectors = training_instance.getArray()
        label = training_instance.getLabel()

        datum = caffe_pb2.Datum()
        datum.channels, datum.height, datum.width = vectors.shape
        datum.label = label
        datum.float_data.extend(vectors.flat)

        self.__batch.Put(str(self.__index), datum.SerializeToString())

        self.__index += 1
        self.__current_batch_size += 1

        if (self.__current_batch_size == self.batchsize):
            self.__db.Write(self.__batch, sync = True)
            self.__batch = None
            self.__current_batch_size = 0

    def close(self):
        if (self.__batch):
            self.__db.Write(self.__batch, sync = True)
            self.__batch = None
        self.__current_batch_size = 0
        self.__db = None

    def read(self, key):
        return self.__db.Get(key)

def main(args):
    ### writing
    ldbCreation = CreateLevelDB(args.dbfile)

    # write single instance
    instance = DummyTrainingInstance()
    ldbCreation.writeTrainingInstance(instance)

    # write list
    training_instance_list = []
    for i in range(0, 1000):
        training_instance_list += DummyTrainingInstance(),
    ldbCreation.writeTrainingInstanceList(training_instance_list)

    # close after you are done!
    ldbCreation.close()

    ### reading (for debug)
    ldbCreation = CreateLevelDB(args.dbfile)
    datum = caffe_pb2.Datum()
    datum.ParseFromString(ldbCreation.read("1"))
    print datum
    print datum.label

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Write a test file.')
    parser.add_argument('dbfile', help='path to a level db test directory')
    args = parser.parse_args()
    main(args)