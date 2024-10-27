
# This class is used to handle file operations such as breaking down a file into chunks and reassembling it
class FileHandler:
    
    # This function breaks down a file into chunks of a specified size and yealds them (Generator)
    # Example of how to use:
    # chunks = file_handler.break_down_file('file_path', chunk_size)
    # for chunk in chunks:
    #     # Do something with the chunk
    @staticmethod
    def break_down_file_generator(file_path, chunk_size):
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
    @staticmethod
    def break_down_file(file_path, chunk_size):
        with open(file_path, 'rb') as f:
            chunks = []
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunks.append(chunk)
            return chunks
        
    @staticmethod
    def extract_name_from_path(file_path: str):
        return file_path.split('/')[-1]
    
    # Example of how to use:
    # file_handler.reasseble_file(chunks, 'file_path')
    @staticmethod
    def reasseble_file(file_path, chunks):
        with open(file_path, 'wb') as f:
            for chunk in chunks:
                f.write(chunk)
                