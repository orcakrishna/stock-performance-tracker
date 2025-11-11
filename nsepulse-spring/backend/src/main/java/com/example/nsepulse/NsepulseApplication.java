package com.example.nsepulse;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class NsepulseApplication {

	public static void main(String[] args) {
		SpringApplication.run(NsepulseApplication.class, args);
	}

}
