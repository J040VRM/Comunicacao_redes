//
//  File.swift
//  projeto_redes
//
//  Created by João Vitor Rocha Miranda on 26/09/25.
//

import Foundation
import Fluent
import Vapor

struct MessageController: RouteCollection{
    func boot(routes: any RoutesBuilder) throws {
        let messages = routes.grouped("messages")
        messages.get(use: index)
        messages.post(use: create)
        messages.patch("message", use: updateMessage)
        
        messages.group(":id") { msg in
            msg.get(use: show)
            msg.delete(use: delete)
        }
    }
    
    func index(req: Request) async throws -> [MessageDTO] {
        try await Message.query(on: req.db).all().map { $0.toDTO() }
    }
    
    func create(req: Request) async throws -> MessageDTO {
        let message = try req.content.decode(Message.self)
        try await message.save(on: req.db)
        return message.toDTO()
    }
    
    func show(req: Request) async throws -> MessageDTO {
        guard let message = try await Message.find(req.parameters.get("id"), on: req.db) else {
            throw Abort(.notFound)
        }
        return message.toDTO()
    }
    
    func delete(req: Request) async throws -> HTTPStatus {
        guard let message = try await Message.find(req.parameters.get("id"), on: req.db) else {
            throw Abort(.notFound)
        }
        try await message.delete(on: req.db)
        return .ok
    }
    
    func updateMessage(req: Request) async throws -> MessageDTO {
        
        let create = try req.content.decode(MessageDTO.UpdateMessage.self)
        guard let message = try await Message.find(create.messageId, on: req.db) else {
            throw Abort(.notFound)
        }
        
        message.message = create.updatedMessage
        try await message.update(on: req.db)
        
        return message.toDTO()
    }
}

