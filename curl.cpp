#include <stdio.h> 
#include <string.h> 
#include <sys/stat.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <netdb.h> 
#include <netinet/in.h> 
#include <arpa/inet.h>
#include <stdlib.h> 
#include <unistd.h> 
#include <fcntl.h> 
#include <sys/stat.h> 

char response[] = "HTTP/1.1 200 OK\n\
Connection:keep-alive\n\
Content-Length:939\n\
Content-Type:text/html\n\
Date:Tue, 02 Aug 2016 20:32:56 GMT\n\
If-Modified-Since:Sat, 30 Jul 2016 16:00:00 GMT\n\
Load-Balancing:web06\n\
Load-Balancing:web06\n\r\n";

class QFILE {
	char buf[100000];
	int length;

	int get_filesz(const char *name)
	{
		struct stat tmp;  
		if(stat(name, &tmp)<0)  
			return 0;  
		return tmp.st_size;  
	}

public:
	void load(const char *name)
	{
		FILE *fp = fopen(name, "r");
		length = get_filesz(name);
		fread(buf, length, 1, fp);
	}

	char * read()
	{
		return (char *)buf;
	}

	int size()
	{
		return length;
	}
};

int main() 
{
	int fd;
	struct sockaddr_in my_addr;
	struct sockaddr_in remote_addr;
	
	my_addr.sin_family = AF_INET;
	my_addr.sin_addr.s_addr = INADDR_ANY;
	my_addr.sin_port = htons(8080);

	int server_fd = socket(PF_INET, SOCK_STREAM, 0);
	bind(server_fd, (sockaddr *)&my_addr, sizeof(struct sockaddr_in));

	listen(server_fd, 5);
	char buf[10000];
	QFILE qf;
	qf.load("main.html");
	while(1)
	{
	
		int sin_size = sizeof(struct sockaddr_in);
		int client_fd = accept(server_fd, (struct sockaddr *)&remote_addr, (socklen_t*)&sin_size);
		printf("accept client %s\n", inet_ntoa(remote_addr.sin_addr));
		memset(buf, 0, sizeof(buf));
		recv(client_fd, buf, sizeof(buf), 0);
		printf("%s\n", buf);

		send(client_fd, response, sizeof(response), 0);
		send(client_fd, qf.read(), qf.size(), 0);

		memset(buf, 0, sizeof(buf));
		recv(client_fd, buf, sizeof(buf), 0);
		printf("%s\n", buf);
		close(client_fd);
	}

	return 0; 
}
