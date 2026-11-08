import grpc
import os
import sys

# Adiciona a pasta proto ao path para encontrar os arquivos gerados
sys.path.append(os.path.join(os.path.dirname(__file__), '../proto'))
import file_processor_pb2
import file_processor_pb2_grpc

def compress_pdf(stub, input_file_path, output_file_path):
    def file_iterator():
        file_name = os.path.basename(input_file_path)
        with open(input_file_path, 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                file_chunk = file_processor_pb2.FileChunk(content=chunk)
                yield file_processor_pb2.FileRequest(
                    file_name=file_name,
                    file_content=file_chunk,
                    compress_pdf_params=file_processor_pb2.CompressPDFRequest()
                )

    print(f"Enviando '{input_file_path}' para o servidor...")
    try:
        response_stream = stub.CompressPDF(file_iterator())
        
        with open(output_file_path, 'wb') as output_file:
            for response in response_stream:
                if not response.success and response.status_message:
                    print(f"Erro no servidor: {response.status_message}")
                    return
                if response.HasField("file_content"):
                    output_file.write(response.file_content.content)
                    
        print(f"Sucesso! PDF comprimido e salvo em: {output_file_path}")
    except grpc.RpcError as e:
        print(f"Erro gRPC ao comprimir PDF: {e.details()}")

def run_client():
    input_pdf = "input.pdf"
    output_pdf = "compressed_output.pdf"

    # Cria um PDF "falso" rápido só para testar a comunicação, caso você não tenha um PDF real na pasta
    if not os.path.exists(input_pdf):
        with open(input_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n%Dummy PDF criado pelo script para teste.\n")
            
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = file_processor_pb2_grpc.FileProcessorServiceStub(channel)
        compress_pdf(stub, input_pdf, output_pdf)

if __name__ == '__main__':
    run_client()